<?php

namespace Tomodomo\Controllers;

use Pimple\Container;

class BaseController
{
    /**
     * @var Container
     */
    public $container;

    /**
     * @param Container $container
     *
     * @return void
     */
    public function __construct(Container $container)
    {
        // Grab the Pimple container
        $this->container = $container;

        // Make Twig available for convenience
        $this->twig = $this->container['twig'];

        return;
    }
}
